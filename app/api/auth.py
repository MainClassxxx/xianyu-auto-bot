"""
用户认证系统
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import random
import string
import base64
import io
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.services.xianyu_oauth import xianyu_oauth

router = APIRouter(prefix="/api/auth", tags=["认证"])

# 配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

# 密码加密（使用 pbkdf2 避免 bcrypt 版本兼容问题）
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# 验证码存储（生产环境应该用 Redis）
verification_codes = {}

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    captcha: str
    captcha_id: str
    email_code: Optional[str] = None
    invite_code: Optional[str] = None  # 邀请码（预留）

class UserLogin(BaseModel):
    username: str
    password: str
    captcha: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

class CaptchaResponse(BaseModel):
    captcha_id: str
    captcha_image: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/captcha")
async def get_captcha():
    """获取图形验证码"""
    captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    # 生成简单验证码（生产环境应该用 PIL 生成图片）
    captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    verification_codes[f"captcha_{captcha_id}"] = {
        "code": captcha_code.lower(),
        "expire": datetime.now() + timedelta(minutes=5)
    }
    
    return {
        "captcha_id": captcha_id,
        "captcha_image": f"data:image/png;base64,{captcha_code}"  # 简化实现
    }

@router.post("/send-email-code")
async def send_email_code(
    email: EmailStr,
    captcha: str,
    captcha_id: str,
    db: Session = Depends(get_db)
):
    """发送邮箱验证码"""
    # 验证图形验证码
    captcha_key = f"captcha_{captcha_id}"
    if captcha_key not in verification_codes:
        raise HTTPException(status_code=400, detail="验证码已过期")
    
    stored_captcha = verification_codes[captcha_key]
    if stored_captcha["code"] != captcha.lower():
        raise HTTPException(status_code=400, detail="图形验证码错误")
    
    # 检查邮箱是否已注册
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="邮箱已注册")
    
    # 生成邮箱验证码
    email_code = ''.join(random.choices(string.digits, k=6))
    verification_codes[f"email_{email}"] = {
        "code": email_code,
        "expire": datetime.now() + timedelta(minutes=10)
    }
    
    # TODO: 实际发送邮件
    # await send_email(email, email_code)
    
    return {"message": "验证码已发送", "debug_code": email_code}  # debug_code 仅用于测试

@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    # 验证图形验证码
    captcha_key = f"captcha_{user_data.captcha_id}"
    if captcha_key not in verification_codes:
        raise HTTPException(status_code=400, detail="验证码已过期")
    
    stored_captcha = verification_codes[captcha_key]
    if stored_captcha["code"] != user_data.captcha.lower():
        raise HTTPException(status_code=400, detail="图形验证码错误")
    
    # 验证邮箱验证码
    if not user_data.email_code:
        raise HTTPException(status_code=400, detail="需要邮箱验证码")
    
    email_key = f"email_{user_data.email}"
    if email_key not in verification_codes:
        raise HTTPException(status_code=400, detail="邮箱验证码已过期")
    
    stored_email_code = verification_codes[email_key]
    if stored_email_code["code"] != user_data.email_code:
        raise HTTPException(status_code=400, detail="邮箱验证码错误")
    
    # 检查用户名/邮箱是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="邮箱已注册")
    
    # 创建用户
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 生成 Token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != "active":
        raise HTTPException(status_code=403, detail="账号已被禁用")
    
    # 生成 Token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "avatar": user.avatar
        }
    }

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "avatar": current_user.avatar,
        "created_at": current_user.created_at
    }

@router.post("/xianyu/qr")
async def create_xianyu_qr_login(
    headless: bool = False,
    db: Session = Depends(get_db)
):
    """创建闲鱼二维码登录会话"""
    import uuid
    
    session_id = str(uuid.uuid4())
    
    try:
        # 创建登录会话
        login_url = await xianyu_oauth.create_login_session(session_id, headless=headless)
        
        # 生成登录二维码
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(login_url)
        qr.make(fit=True)
        
        # 生成二维码图片
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        return {
            "session_id": session_id,
            "qr_code": f"data:image/png;base64,{qr_base64}",
            "login_url": login_url,
            "message": "请使用闲鱼 APP 扫描二维码登录"
        }
    except Exception as e:
        logger.error(f"创建二维码登录失败：{e}")
        raise HTTPException(status_code=500, detail=f"创建登录会话失败：{str(e)}")

@router.get("/xianyu/{session_id}/status")
async def get_xianyu_qr_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """检查闲鱼二维码登录状态"""
    try:
        result = await xianyu_oauth.check_login_status(session_id)
        
        if result["status"] == "not_found":
            raise HTTPException(status_code=404, detail="会话不存在")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"检查登录状态失败：{e}")
        raise HTTPException(status_code=500, detail=f"检查登录状态失败：{str(e)}")

@router.delete("/xianyu/{session_id}")
async def cancel_xianyu_qr_session(
    session_id: str
):
    """取消闲鱼登录会话"""
    try:
        await xianyu_oauth.close_session(session_id)
        return {"success": True, "message": "会话已关闭"}
    except Exception as e:
        logger.error(f"关闭会话失败：{e}")
        raise HTTPException(status_code=500, detail=f"关闭会话失败：{str(e)}")

@router.post("/xianyu/test-cookie")
async def test_xianyu_cookie(
    cookie: str,
    db: Session = Depends(get_db)
):
    """测试闲鱼 Cookie 是否有效"""
    from app.services.xianyu_api import xianyu_manager
    
    try:
        # 创建临时客户端测试
        device_id = f"test_{int(datetime.now().timestamp())}"
        client = xianyu_manager.XianyuClient(cookie, device_id)
        is_valid = await client.test_connection()
        
        if is_valid:
            return {
                "valid": True,
                "message": "Cookie 有效",
                "account_info": client.account_info
            }
        else:
            return {
                "valid": False,
                "message": "Cookie 无效，无法连接闲鱼"
            }
    except Exception as e:
        logger.error(f"测试 Cookie 失败：{e}")
        return {
            "valid": False,
            "message": f"测试失败：{str(e)}"
        }
   "valid": True,
                "message": "Cookie 有效",
                "account_info": client.account_info
            }
        else:
            return {
                "valid": False,
                "message": "Cookie 无效，无法连接闲鱼"
            }
    except Exception as e:
        logger.error(f"测试 Cookie 失败：{e}")
        return {
            "valid": False,
            "message": f"测试失败：{str(e)}"
        }
          "valid": False,
            "message": f"测试失败：{str(e)}"
        }
ue,
                "message": "Cookie 有效",
                "account_info": client.account_info
            }
        else:
            return {
                "valid": False,
                "message": "Cookie 无效，无法连接闲鱼"
            }
    except Exception as e:
        logger.error(f"测试 Cookie 失败：{e}")
        return {
            "valid": False,
            "message": f"测试失败：{str(e)}"
        }
