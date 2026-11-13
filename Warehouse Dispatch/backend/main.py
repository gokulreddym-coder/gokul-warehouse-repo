from fastapi import FastAPI, HTTPException, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import functions
 
app = FastAPI(
    title = "Warehouse Dispatch Management System",
    description = "Warehouse Dispatches"
)
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)
 
VALID_STATUSES = ["pending", "received", "dispatched"]
VALID_BATCH_STATUSES = ["pending", "dispatched"]
 
@app.post("/packages")
def register_package(package_name: str, destination: str, weight: float, arrival_date: date, status: str):
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    return functions.register_package(package_name=package_name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
 
@app.get("/packages")
def search_packages(destination=None, status=None, arrival_date: date = None , token=Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token.")
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    return functions.search_packages(destination=destination, status=status, arrival_date=arrival_date)
 
@app.get("/packages/{id}")
def get_one_package(id: int):
    result = functions.get_one_package(id=id)
    if not result:
        raise HTTPException(status_code=404, detail="Package not found")
    return result
 
@app.patch("/packages/{id}")
def update_package(id: int, package_name: str = None, destination: str = None, weight: float = None, arrival_date: date = None, status: str = None,token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token.")
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status.")
    result = functions.update_package(id=id, package_name=package_name, destination=destination, weight=weight, arrival_date=arrival_date, status=status)
    if not result:
        raise HTTPException(status_code=404, detail="Package not found")
    return result
 
@app.delete("/packages/{id}")
def delete_package(id: int,token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token.")
    package = functions.get_one_package(id=id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    if package["status"] == "dispatched":
        raise HTTPException(status_code=400, detail="Dispatched package cannot be deleted")
    return functions.delete_package(id=id)
 
@app.get("/batches")
def search_batches(destination=None, vehicle=None, dispatch_status=None,token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token.")
    if dispatch_status and dispatch_status not in VALID_BATCH_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid dispatch status.")
    return functions.search_batches(destination=destination, vehicle=vehicle, dispatch_status=dispatch_status)

@app.post("/batches")
def create_batch(package_ids,destination: str, vehicle: str, dispatch_status: str = "pending",token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token.")
    if dispatch_status not in VALID_BATCH_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid dispatch status.")
    result, missing_id = functions.create_batch(destination=destination, vehicle=vehicle, dispatch_status=dispatch_status, package_ids=package_ids)
    if missing_id is not None:
        raise HTTPException(status_code=404, detail=f"Package {missing_id} not found")
    return result

@app.get("/stats")
def get_warehouse_stats(token = Header(None)):
    username = functions.verify_token(token=token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or Expired Token.")
    return functions.get_warehouse_stats()


@app.post("/login")
def login(username = Body(),password = Body()):
    token = functions.verify_login(username=username,password=password)
    if not token:
        raise HTTPException(status_code=401,detail="Invalid Credentials")
    return token

@app.post("/refresh")
def refresh(refresh_token):
    username = functions.verify_token(token=refresh_token,tokentype="refresh")
    if not username:
        raise HTTPException(status_code=401,detail="Invalid Token")
    access_token = functions.create_token(username=username , tokentype="access")
    return {"access_token":access_token}

@app.post("/register")
def register(username = Body(),password = Body()):
    if functions.register_user(user_name=username,password=password):
        return {"message":"user registered successfully"}
    raise HTTPException(status_code=400 , detail= "User already exists")