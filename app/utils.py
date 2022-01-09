from passlib.context import CryptContext


# tells passlib which hashing algorithm to use for password encryption
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def hash(pwd: str):
    return pwd_context.hash(pwd)


# the .verify() method automatically handles comparing the non-hashed hashed passwords
def verify(plain_pwd, hash_pwd):
    return pwd_context.verify(plain_pwd, hash_pwd)
