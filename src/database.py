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
        if user: 
            print(f"Usuario {user.name} ha iniciado sesión correctamente. Movilidad reducida: {user.reduced_mobility}")
            return user
        print("Usuario o contraseña incorrectos.")
        return None

        