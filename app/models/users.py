from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    USER = "user"


# CompanyType Enum
class CompanyType(str, Enum):
    EI = "Entrepreneur individuel (EI) (y compris micro-entrepreneur)"
    EURL = "Entreprise unipersonnelle à responsabilité limitée (EURL)"
    SARL = "Société à responsabilité limitée (SARL)"
    SASU = "Société par actions simplifiée unipersonnelle (SASU)"
    SAS = "Société par actions simplifiée (SAS)"
    SA = "Société anonyme (SA)"
    SNC = "Société en nom collectif (SNC)"
    SCS = "Société en commandite simple (SCS)"
    SCA = "Société en commandite par actions (SCA)"


class OrganisationBase(SQLModel):
    company_type: CompanyType | None = None
    company_name: str | None = None
    company_trigram: str | None = None  # Added trigram
    trade_name: str | None = None
    logo: str | None = None  # URL or path to the logo file
    website: str | None = None
    siren_number: int | None = None
    ape_code: str | None = None
    share_capital: float | None = None
    start_date: datetime | None = None
    registration_date: datetime | None = None
    headquarter_siret_number: int | None = None
    address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    standard_seller_fees: int | None = None
    standard_buyer_fees: int | None = None
    expert_fees: int | None = None

class Organisation(OrganisationBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    users: list["User"] | None = Relationship(back_populates="organisation")
    # clients: list['Client'] | None = Relationship(back_populates='organisation')
    # sales: list['Sale'] | None = Relationship(back_populates='organisation')
    # lots: list['Lot'] | None = Relationship(back_populates='organisation')
    # invoices: list['Invoice'] | None = Relationship(back_populates='organisation')
    # payments: list['Payment'] | None = Relationship(back_populates='organisation')



class OrganisationCreate(OrganisationBase):
    company_name: str


class OrganisationRead(OrganisationBase):
    id: int | None = None
    siren_number: int | None = None
    ape_code: str | None = None
    share_capital: float | None = None
    start_date: datetime | None = None
    registration_date: datetime | None = None
    headquarter_siret_number: int | None = None
    address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    standard_seller_fees: int | None = None
    standard_buyer_fees: int | None = None
    expert_fees: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class OrganisationUpdate(SQLModel):
    company_type: CompanyType | None = None
    company_name: str | None = None
    company_trigram: str | None = None  # Added trigram
    trade_name: str | None = None
    logo: str | None = None
    website: str | None = None
    siren_number: int | None = None
    ape_code: str | None = None
    share_capital: float | None = None
    start_date: datetime | None = None
    registration_date: datetime | None = None
    headquarter_siret_number: int | None = None
    address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    standard_seller_fees: int | None = None
    standard_buyer_fees: int | None = None
    expert_fees: int | None = None

class UserOrganisationLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    organisation_id: int = Field(foreign_key="organisation.id", primary_key=True)
    role: UserRole
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserBase(SQLModel):
    email: str = Field(unique=True)
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_staff: bool | None = False


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    organisation_id: int = Field(default=None, foreign_key="organisation.id")
    organisation: "Organisation" = Relationship(back_populates="users")


class UserCreate(UserBase):
    email: str
    password: str
    first_name: str
    last_name: str

class UserRegister(UserCreate):
    password_confirm: str


class UserRead(UserBase):
    id: int
    created_at: datetime | None
    updated_at: datetime | None


class UserUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None


class UserUpdateMe(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zipcode: str | None = None
    country: str | None = None


class UpdatePassword(SQLModel):
    old_password: str
    new_password: str
    new_password_confirm: str


class UserPublic(SQLModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    city: str | None = None
    country: str | None = None
