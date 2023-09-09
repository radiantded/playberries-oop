from dataclasses import dataclass

from pydantic import BaseModel

from config import PROXY_LOGIN, PROXY_PASS


class Proxy(BaseModel):
    ip: str
    port: int
    login: str = PROXY_LOGIN
    password: str = PROXY_PASS 
    
    
class Response(BaseModel):
    status: str
    list: dict[str, Proxy]


@dataclass
class Task:
    _id: int
    prompt: str
    item_id: int
    cycles: int
    skip_carts: int
