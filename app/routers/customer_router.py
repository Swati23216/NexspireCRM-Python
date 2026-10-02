from fastapi import APIRouter, Depends, HTTPException, status

from app.models.customer import Customer
from app.models.customer_schema import (
    CustomerCreate,
    CustomerUpdate
)

from app.core.dependencies import require_permission


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


# =========================================================
# CREATE CUSTOMER
# =========================================================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    current_user=Depends(require_permission("customers.create"))
):

    # Check duplicate email
    existing_customer = await Customer.find_one(
        Customer.email == data.email
    )

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer with this email already exists"
        )

    # Generate numeric customer_id
    last_customer = await Customer.find_all().sort(
        "-customer_id"
    ).first_or_none()

    if last_customer:
        new_customer_id = last_customer.customer_id + 1
    else:
        new_customer_id = 1

    customer = Customer(
        customer_id=new_customer_id,
        name=data.name,
        email=data.email,
        phone=data.phone,
        company=data.company,
        address=data.address,
        city=data.city,
        state=data.state,
        source=data.source,
        created_by=current_user["user_id"],
        is_active=True
    )

    await customer.insert()

    return {
        "message": "Customer created successfully",
        "customer_id": customer.customer_id
    }


# =========================================================
# SEARCH CUSTOMERS
# =========================================================

@router.get("/search/{name}")
async def search_customers(
    name: str,
    current_user=Depends(require_permission("customers.view"))
):

    customers = await Customer.find(
        {
            "name": {
                "$regex": name,
                "$options": "i"
            }
        }
    ).to_list()

    return customers


# =========================================================
# GET ALL CUSTOMERS
# =========================================================

@router.get("/")
async def get_customers(
    current_user=Depends(require_permission("customers.view"))
):

    customers = await Customer.find_all().to_list()

    return customers


# =========================================================
# GET CUSTOMER BY NUMERIC CUSTOMER ID
# =========================================================

@router.get("/{customer_id}")
async def get_customer(
    customer_id: int,
    current_user=Depends(require_permission("customers.view"))
):

    customer = await Customer.find_one(
        Customer.customer_id == customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer


# =========================================================
# UPDATE CUSTOMER
# =========================================================

@router.put("/{customer_id}")
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    current_user=Depends(require_permission("customers.update"))
):

    customer = await Customer.find_one(
        Customer.customer_id == customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # -----------------------------------------------------
    # Update name
    # -----------------------------------------------------

    if data.name is not None:
        customer.name = data.name

    # -----------------------------------------------------
    # Update email
    # -----------------------------------------------------

    if data.email is not None:

        existing_customer = await Customer.find_one(
            Customer.email == data.email
        )

        if (
            existing_customer
            and existing_customer.customer_id != customer_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already belongs to another customer"
            )

        customer.email = data.email

    # -----------------------------------------------------
    # Update phone
    # -----------------------------------------------------

    if data.phone is not None:
        customer.phone = data.phone

    # -----------------------------------------------------
    # Update company
    # -----------------------------------------------------

    if data.company is not None:
        customer.company = data.company

    # -----------------------------------------------------
    # Update address
    # -----------------------------------------------------

    if data.address is not None:
        customer.address = data.address

    # -----------------------------------------------------
    # Update city
    # -----------------------------------------------------

    if data.city is not None:
        customer.city = data.city

    # -----------------------------------------------------
    # Update state
    # -----------------------------------------------------

    if data.state is not None:
        customer.state = data.state

    # -----------------------------------------------------
    # Update source
    # -----------------------------------------------------

    if data.source is not None:
        customer.source = data.source

    # -----------------------------------------------------
    # Update active status
    # -----------------------------------------------------

    if data.is_active is not None:
        customer.is_active = data.is_active

    await customer.save()

    return {
        "message": "Customer updated successfully",
        "customer": customer
    }


# =========================================================
# DELETE CUSTOMER
# ADMIN ONLY
# =========================================================

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    current_user=Depends(require_permission("customers.delete"))
):

    customer = await Customer.find_one(
        Customer.customer_id == customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    await customer.delete()

    return {
        "message": "Customer deleted successfully",
        "customer_id": customer_id
    }
