from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()




async def get_db():
    async with AsyncSessionLocal() as session:
        yield session




async def create_tables():
    """Create all database tables defined in models if they don't exist"""
    try:
        # Import the models here to avoid circular imports
        # These imports ensure the models are registered with Base
        from app.core.models import Violation, ScannedUser
        
        async with engine.begin() as conn:
            # Create tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        raise
