run:
	@uvicorn workoutapi.main:app --reload

create-migrations:
	alembic revision --autogenerate -m $(d)

rum-migrations:
	@PYTHONPATH=$PYTHONPATH:$(pwd) alembic upgrade head