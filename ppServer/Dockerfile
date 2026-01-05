# pull official base image
FROM dhi.io/python:3.14-alpine3.22-dev AS builder


##### folder structure ######

# create the appropriate directories
WORKDIR /var
ENV PATH="/var/deps/bin:$PATH"


##### PIP ######

RUN python -m venv ./deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


##### NPM ######

# install
RUN apk add --update npm

# Copy config
COPY package.json ./

# install tools
RUN npm install --no-package-lock

# copy project to work on
COPY backend www/

##### -> SASS ######
RUN npx sass ./www --update --no-source-map

# ##### -> TS ######

# Copy config
COPY tsconfig.json ./
RUN npx tsc --project ./ || true



# Runtime stage
FROM dhi.io/python:3.14-alpine3.22 AS runtime
LABEL version="5.2"

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/var/deps/bin:$PATH"

USER nonroot:nonroot

# Set the working directory in the container
WORKDIR /var/www


# Install Python packages from the build-stage wheels
COPY --from=builder --chown=nonroot:nonroot /var/deps /var/deps/


# copy all application files
COPY --from=builder --chown=nonroot:nonroot /var/www /var/www/


# Set the entrypoint to start the application
COPY --chown=nonroot:nonroot entrypoint.*.py gunicorn.conf.py ./
ENTRYPOINT ["python"]
CMD ["entrypoint.prod.py"]
