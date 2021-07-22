glucose:
	@cd glucose-syrup-4.1/simp; $(MAKE)
	@cp glucose-syrup-4.1/simp/glucose ./glucose

.PHONY: clean
clean:
	@cd glucose-syrup-4.1/simp; $(MAKE) clean
	@if test -f "glucose"; then rm glucose; fi