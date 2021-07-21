glucose:
	@cd glucose-syrup-4.1/parallel; $(MAKE) rs
	@cp glucose-syrup-4.1/parallel/glucose-syrup_static ./glucose

.PHONY: clean
clean:
	@cd glucose-syrup-4.1/parallel; $(MAKE) clean
	@if test -f "glucose"; then rm glucose; fi