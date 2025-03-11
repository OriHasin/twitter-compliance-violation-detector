from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
import os
import json
from pathlib import Path
from config import UPLOAD_DIR




# Create policy router
policy_router = APIRouter(prefix="/policies", tags=["Policies"])




# Helper function to read policy file
async def load_policy_rules(policy_name: str) -> List[str]:
    """Load policy rules from a JSON file."""
    file_path = os.path.join(UPLOAD_DIR, f"{policy_name}.json")
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Policy file '{policy_name}' not found")
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            
            # Assuming the JSON has a "rules" list
            if isinstance(data, dict) and "rules" in data:
                return data["rules"]
            # Or if it's a list of rules
            elif isinstance(data, list):
                return data
            else:
                raise HTTPException(status_code=400, detail="Invalid policy file format")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in policy file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading policy file: {str(e)}")






@policy_router.post("/upload")
async def upload_policy_file(file: UploadFile = File(...)):
    """Upload a compliance policy file (JSON only)."""
    try:
        # Ensure the file is a JSON file
        if not file.filename.lower().endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate JSON format
        try:
            with open(file_path, "r") as f:
                policy_data = json.load(f)
                
                # Check if it has rules
                if isinstance(policy_data, dict) and "rules" in policy_data:
                    rules_count = len(policy_data["rules"])
                elif isinstance(policy_data, list):
                    rules_count = len(policy_data)
                else:
                    raise ValueError("Policy file must contain rules as a list or a 'rules' key with a list")
                
        except json.JSONDecodeError:
            # Remove invalid file
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except Exception as e:
            # Remove invalid file
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=str(e))
        
        return {
            "message": f"Policy file uploaded successfully",
            "filename": file.filename,
            "rules_count": rules_count
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading policy file: {str(e)}")





@policy_router.get("/list")
async def list_available_policies():
    """List all available compliance policy files."""
    try:
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Get all JSON files in the upload directory
        policy_files = [f.stem for f in Path(UPLOAD_DIR).glob("*.json")]
        
        return {"policies": policy_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing policy files: {str(e)}")





@policy_router.get("/{policy_name}/rules")
async def get_policy_rules(policy_name: str):
    """Get the rules for a specific policy."""
    
    rules = await load_policy_rules(policy_name)
    return {"policy_name": policy_name, "rules": rules}