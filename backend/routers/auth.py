"""Auth Router - Registration, Login, Profile"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta

from backend.database import get_db, settings
from backend.models.user import User, Address
from backend.models.order import Order
from backend.schemas.auth import (
    UserCreate, UserResponse, UserUpdate, AddressCreate, AddressResponse,
    LoginRequest, TokenResponse, RefreshRequest
)
from backend.schemas.order import OrderResponse
from backend.core.auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, get_current_user, get_current_user_required
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user = User(
        email=data.email,
        username=data.username,
        full_name=data.full_name,
        phone=data.phone,
        hashed_password=hash_password(data.password),
        role="customer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create tokens
    token = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        refresh_token=refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    token = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        refresh_token=refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.get(User, int(payload.get("sub")))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or disabled")

    token = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=token,
        refresh_token=new_refresh,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user_required), db: Session = Depends(get_db)):
    db_user = db.get(User, user["id"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(db_user)


@router.put("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    user: dict = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    db_user = db.get(User, user["id"])
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return UserResponse.model_validate(db_user)


@router.get("/addresses", response_model=list[AddressResponse])
async def get_addresses(
    user: dict = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    addresses = db.execute(
        select(Address).where(Address.user_id == user["id"])
    ).scalars().all()
    return [AddressResponse.model_validate(a) for a in addresses]


@router.post("/addresses", response_model=AddressResponse)
async def create_address(
    data: AddressCreate,
    user: dict = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    if data.is_default:
        from sqlalchemy import update
        db.execute(update(Address).where(Address.user_id == user['id']).values(is_default=False))
    address = Address(user_id=user["id"], **data.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return AddressResponse.model_validate(address)


@router.get("/orders", response_model=list[OrderResponse])
async def get_my_orders(
    user: dict = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    orders = db.execute(
        select(Order).where(Order.user_id == user["id"]).order_by(Order.created_at.desc())
    ).scalars().all()
    return orders
