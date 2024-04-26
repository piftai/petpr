all:
	python3 main.py

#clean:
#	rm -rf base.db
#	python3 db.py
#	python3 main.py

clean_verif:
	python3 db_clear_verification_account.py
