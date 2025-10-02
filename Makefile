#!/usr/bin/make

help:
	@echo Avaialble commands:
	@echo     - generate-types:
	@echo         -- Fetch Typescript types from OpenAPI spec of the accesify API.


generate-types:
	bun x openapi-typescript http://localhost:8000/openapi.json -o ./frontend/src/app/types/accesify.d.ts