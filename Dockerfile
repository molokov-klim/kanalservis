#parent image
FROM python:3.8

#copy files to image
COPY . .

#preinstructions
RUN pip install -r req.txt

#port
EXPOSE 9800

#what need to run
CMD [ "python", "main.py" ]