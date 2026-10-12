FROM nexusbioacr.azurecr.io/nexusbio-sandbox-base:latest

WORKDIR /app

# There is no need of this COPY requirements.txt . and RUN pip install --no-cache-dir -r requirements.txt in Dockerfile
# but in case if someone adds a new dependency in requirements.txt and forgets to rebuild the base image
# this will ensure that the new dependency is installed in the container without rebuilding the base image
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app/

EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]