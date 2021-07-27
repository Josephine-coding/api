from fastapi import FastAPI, Depends, HTTPException, status, Security
import pickle
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from database import fake_users_db
from schemas import Token, User
from utils import authenticate_user, create_access_token, get_current_active_user
from utils import ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

#monitoring
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "api_test"})
    )
)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

tracer = trace.get_tracer(__name__)


app = FastAPI()


@app.get("/{input}")
def predict(input: str, current_user: User = Depends(get_current_active_user)):
    if current_user:
        tfidf, model = pickle.load(open('model.bin', 'rb'))
        predictions = model.predict(tfidf.transform([input]))
        label = predictions[0]
        return {'text': input, 'label': label}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Security(get_current_active_user, scopes=["me"])):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(
    current_user: User = Security(get_current_active_user, scopes=["items"])
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/status/")
async def read_system_status(current_user: User = Depends(get_current_user)):
    return {"status": current_user.role}


FastAPIInstrumentor.instrument_app(app)