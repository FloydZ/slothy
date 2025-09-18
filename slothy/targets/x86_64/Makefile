all:
	@if ! [ -f "instructions.xml" ]; then\
		curl -L 'https://www.uops.info/instructions.xml' > "instructions.xml";\
	fi

clean:
	rm -f instructions.xml

