from sqlmodel import Field, Session, SQLModel, create_engine, select


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(index=True, unique=True)
    password: str
    reduced_mobility: bool = False

engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

def register_user(name: str, email: str, password: str, reduced_mobility: bool) -> User | None:
    with Session(engine) as session:
        existente = session.exec(select(User).where(User.email == email)).first()
        if existente:
            raise ValueError(f"El correo {email} ya está registrado.")
            return None

        new_user = User(name=name, email=email, password=password, reduced_mobility=reduced_mobility)      
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

def login(email: str, password: str) -> User | None:
    with Session(engine) as session:
        statement = select(User).where(User.email == email, User.password == password)
        user = session.exec(statement).first()
        return user

def update_user(user_id: int, name: str, email: str, password: str, reduced_mobility: bool) -> User | None:
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no encontrado.")

        # Verificar si el nuevo correo ya está registrado por otro usuario
        existente = session.exec(select(User).where(User.email == email, User.id != user_id)).first()
        if existente:
            raise ValueError(f"El correo {email} ya está registrado por otro usuario.")

        user.name = name
        user.email = email
        user.password = password
        user.reduced_mobility = reduced_mobility

        session.add(user)
        session.commit()
        session.refresh(user)
        return user    