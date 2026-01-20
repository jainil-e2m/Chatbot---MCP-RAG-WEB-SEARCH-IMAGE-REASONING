"""
Authentication API endpoints with Supabase integration.
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse
from app.core.database import supabase
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(tags=["authentication"])


@router.post("/signup", response_model=SignupResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest):
    """
    Register a new user account.
    
    Steps:
    1. Validate password confirmation
    2. Check if email already exists
    3. Hash password
    4. Create user in Supabase
    5. Generate JWT token
    """
    # Validate password confirmation
    if request.password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if user already exists
    existing_user = supabase.table("users").select("id").eq("email", request.email).execute()
    if existing_user.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create user in database
    try:
        result = supabase.table("users").insert({
            "name": request.name,
            "email": request.email,
            "password_hash": password_hash
        })
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        user = result.data[0]
        
        # Generate JWT token
        token = create_access_token(data={
            "sub": user["id"],
            "email": user["email"],
            "name": user["name"]
        })
        
        return SignupResponse(
            user_id=user["id"],
            name=user["name"],
            email=user["email"],
            token=token
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    Steps:
    1. Find user by email
    2. Verify password
    3. Generate JWT token
    """
    # Find user by email
    result = supabase.table("users").select("*").eq("email", request.email).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user = result.data[0]
    
    # Verify password
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Generate JWT token
    token = create_access_token(data={
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"]
    })
    
    return LoginResponse(
        user_id=user["id"],
        name=user["name"],
        email=user["email"],
        token=token
    )
