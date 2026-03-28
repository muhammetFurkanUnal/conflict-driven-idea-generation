from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class APIKEY(BaseModel):
	gemini25flash: str

class Tree(BaseModel):
	depth: int
	leaves: int
	json_file: str

class Thesis(BaseModel):
	limit: int

class Settings(BaseSettings):
	api_key: APIKEY
	tree: Tree
	thesis: Thesis
	debug: bool

	model_config = SettingsConfigDict(
        env_file="./.env", 
        env_nested_delimiter="."
    )

settings = Settings()




