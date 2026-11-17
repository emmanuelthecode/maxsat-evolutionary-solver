# Built on the module's marking image, which runs a battery of tests
# against the program given in -submission.
FROM pklehre/ec2025-lab2

ADD maxsat.py /bin

CMD ["-username", "oei325", "-submission", "python3 /bin/maxsat.py"]
