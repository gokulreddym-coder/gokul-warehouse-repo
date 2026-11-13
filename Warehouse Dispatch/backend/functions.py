from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, create_engine
from sqlalchemy.orm import Session, declarative_base

import jwt
from datetime import datetime , timedelta , timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

engine = create_engine("sqlite:///warehouse.db")
Base = declarative_base()

ph=PasswordHasher()

class DispatchBatch(Base):
    __tablename__ = "dispatch_batches"
    id = Column(Integer, primary_key=True)
    destination = Column(String)
    vehicle = Column(String)
    dispatch_status = Column(String)


class Package(Base):
    __tablename__ = "packages"
    id = Column(Integer, primary_key=True)
    package_name = Column(String)
    destination = Column(String)
    weight = Column(Float)
    arrival_date = Column(Date)
    status = Column(String)
    batch_id = Column(Integer, ForeignKey("dispatch_batches.id"), nullable=True)

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer , primary_key=True)
    user_name = Column(String)
    password = Column(String)


Base.metadata.create_all(engine)


def register_package(package_name, destination, weight, arrival_date, status):
    session = Session(engine)

    pkg = Package(
        package_name=package_name,
        destination=destination,
        weight=float(weight),
        arrival_date=arrival_date,
        status=status
    )
    session.add(pkg)
    session.commit()

    result = {
        "id": pkg.id,
        "package_name": pkg.package_name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": str(pkg.arrival_date),
        "status": pkg.status,
        "batch_id": pkg.batch_id
    }

    session.close()
    return result


def get_one_package(id):
    session = Session(engine)

    pkg = session.query(Package).filter(Package.id == id).first()

    if pkg is None:
        session.close()
        return None

    result = {
        "id": pkg.id,
        "package_name": pkg.package_name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": str(pkg.arrival_date),
        "status": pkg.status,
        "batch_id": pkg.batch_id
    }

    session.close()
    return result


def update_package(id, package_name=None, destination=None, weight=None, arrival_date=None, status=None):
    session = Session(engine)

    pkg = session.query(Package).filter(Package.id == id).first()

    if pkg is None:
        session.close()
        return None

    if package_name is not None:
        pkg.package_name = package_name

    if destination is not None:
        pkg.destination = destination

    if weight is not None:
        pkg.weight = float(weight)

    if arrival_date is not None:
        pkg.arrival_date = arrival_date

    if status is not None:
        pkg.status = status

    session.commit()

    result = {
        "id": pkg.id,
        "package_name": pkg.package_name,
        "destination": pkg.destination,
        "weight": pkg.weight,
        "arrival_date": str(pkg.arrival_date),
        "status": pkg.status,
        "batch_id": pkg.batch_id
    }

    session.close()
    return result


def delete_package(id):
    session = Session(engine)

    pkg = session.query(Package).filter(Package.id == id).first()

    if pkg is None:
        session.close()
        return None

    if pkg.status == "dispatched":
        session.close()
        return None

    session.delete(pkg)
    session.commit()

    session.close()
    return True


def search_packages(destination=None, status=None, arrival_date=None):
    session = Session(engine)

    query = session.query(Package)

    if destination is not None:
        query = query.filter(Package.destination == destination)

    if status is not None:
        query = query.filter(Package.status == status)

    if arrival_date is not None:
        query = query.filter(Package.arrival_date == arrival_date)

    packages = query.all()

    result = []

    for pkg in packages:
        result.append({
            "id": pkg.id,
            "package_name": pkg.package_name,
            "destination": pkg.destination,
            "weight": pkg.weight,
            "arrival_date": str(pkg.arrival_date),
            "status": pkg.status,
            "batch_id": pkg.batch_id
        })

    session.close()
    return result


def search_batches(destination=None, vehicle=None, dispatch_status=None):
    session = Session(engine)

    query = session.query(DispatchBatch)

    if destination is not None:
        query = query.filter(DispatchBatch.destination == destination)

    if vehicle is not None:
        query = query.filter(DispatchBatch.vehicle == vehicle)

    if dispatch_status is not None:
        query = query.filter(DispatchBatch.dispatch_status == dispatch_status)

    batches = query.all()

    result = []

    for batch in batches:
        packages = session.query(Package).filter(Package.batch_id == batch.id).all()

        package_ids = []
        for pkg in packages:
            package_ids.append(pkg.id)

        result.append({
            "id": batch.id,
            "destination": batch.destination,
            "vehicle": batch.vehicle,
            "dispatch_status": batch.dispatch_status,
            "package_ids": package_ids
        })

    session.close()
    return result


def create_batch(destination, vehicle, dispatch_status="pending", package_ids=None):
    session = Session(engine)

    packages = []
    if package_ids:
        for pid in package_ids:
            pkg = session.query(Package).filter(Package.id == pid).first()
            if pkg is None:
                session.close()
                return None, pid
            packages.append(pkg)

    batch = DispatchBatch(
        destination=destination,
        vehicle=vehicle,
        dispatch_status=dispatch_status
    )
    session.add(batch)
    session.commit()

    assigned_ids = []
    for pkg in packages:
        pkg.batch_id = batch.id
        if dispatch_status == "dispatched":
            pkg.status = "dispatched"
        assigned_ids.append(pkg.id)

    session.commit()

    result = {
        "id": batch.id,
        "destination": batch.destination,
        "vehicle": batch.vehicle,
        "dispatch_status": batch.dispatch_status,
        "package_ids": assigned_ids
    }

    session.close()
    return result, None


def get_warehouse_stats():
    session = Session(engine)

    packages = session.query(Package).all()

    total_received = len(packages)
    total_dispatched = 0
    total_pending = 0
    destination_counts = {}

    for pkg in packages:
        if pkg.status == "dispatched":
            total_dispatched += 1
        else:
            total_pending += 1

        destination_counts[pkg.destination] = destination_counts.get(pkg.destination, 0) + 1

    session.close()
    return {
        "total_packages_received": total_received,
        "total_packages_pending": total_pending,
        "total_packages_dispatched": total_dispatched,
        "destination_wise_count": destination_counts
    }


USERNAME = "admin"
PASSWORD = "admin123"

ACESSS_TOKEN_EXPIRY = 15
REFRESH_TOKEN_EXPIRY = 7 * 24 
SECRET_KEY = "123SECRET"
ALGORITHM = "HS256"


def verify_login(username,password):
    session=Session(engine)
    query = session.query(Users).filter(Users.user_name == username).first()
    if query is None:
        session.close()
        return False
    try:
        ph.verify(query.password,password)
    except VerifyMismatchError:
        session.close()
        return False
    session.close()
    access_token = create_token(username=username, tokentype = "access")
    refresh_token = create_token(username=username , tokentype="refresh")
    return {"access_token":access_token,"refresh_token":refresh_token}
 
def create_token(username:str,tokentype:str):
    if tokentype == "access":
        payload={
            "username":username,
            "tokentype":tokentype,
            "exp" :datetime.now(timezone.utc) + timedelta(minutes=ACESSS_TOKEN_EXPIRY)
        }
    elif tokentype == "refresh":
        payload={
            "username":username,
            "tokentype":tokentype,
            "exp" :datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRY)
        }

    token = jwt.encode(payload=payload,key=SECRET_KEY,algorithm=ALGORITHM)
    return token
    
def verify_token(token,tokentype="access"):
    try:
        payload = jwt.decode(jwt=token,key=SECRET_KEY,algorithms=[ALGORITHM])
    except Exception:
        return False

    if payload["tokentype"] == tokentype:
        return payload["username"]
    return False

def register_user(user_name:str,password:str):
    session = Session(engine)
    user_exits=session.query(Users).filter_by(user_name=user_name).first()
    if user_exits is not None:
        session.close()
        return False
    session.add(Users(user_name=user_name,password=ph.hash(password)))
    session.commit()
    session.close()
    return True