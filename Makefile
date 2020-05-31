all:
	@echo
	@echo Usage:
	@echo
	@echo "     make push"
	@echo

push:
	git commit -am "code update by `whoami` on `date`"
	git push

clean:
	rm -rf ~/tmp/*
