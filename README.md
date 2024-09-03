# Online Coursework to pdf

- I do have an kindle
- It was summer until 3 days ago
- Coursework for the module i did in summer was not printed
  - instead, on a website, 3 clicks required to get a readable version
- kindle browser sucks
- i want pdf of my course materials to learn at the beach

Not sure this is fully permitted by the uni, if you use this script, definitly DO NOT SHARE THE RESULTING PDF with anyone and DO NOT UPLOAD THE PDF ANYWHERE

## how to use

- edit the variable COURSE_WEBSITE in the moduleToPDF.py
- run the ./setup.sh script
- close all chrome windows and launch chrome with `--remote-debugging-port=9222`
- run `python3 moduleToPdf.py`

- doublecheck the newly created pdf (`coursework_ebook_final.pdf`) countains everything you expect, in an logical order!
- move the pdf file to your epaper device

## caveats

- sometimes a few pages are double and in front of the other pages - i am to lazy to fix this
- this only works for module content already accessible, obviously
- this is clunky and should be cleaned up

## sources / credits

claude.ai did the first 80%
