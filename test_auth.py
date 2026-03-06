import sys
sys.path.append('backend')

print("Testing auth imports...")

try:
    from app.auth.models import User
    print("✅ Auth models imported")
    
    from app.auth.schemas import UserCreate
    print("✅ Auth schemas imported")
    
    from app.auth.utils import get_password_hash, create_access_token
    print("✅ Auth utils imported")
    
    from app.auth.router import router
    print("✅ Auth router imported")
    
    # Test password hashing
    test_hash = get_password_hash("testpassword")
    print(f"✅ Password hashing works: {test_hash[:20]}...")
    
    # Test token creation
    token = create_access_token(data={"sub": "test@example.com"})
    print(f"✅ Token creation works: {token[:30]}...")
    
    print("\n" + "="*50)
    print("✅ STEP 3 COMPLETE - Auth system ready!")
    print("="*50)
    
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()