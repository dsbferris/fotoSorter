# The problem
I wanted to copy my Google Photos (and Video) over to iCloud due to switch from Android to iPhone.
Therefor I got myself a "takeout" from Google, a privacy and backup feature. INSERT LINK!

Sadly copying all photos and videos into iCloud, either on Windows, Web, Mac,
results in all being timestamped on the date downloaded/unpacked.

All images were displayed at this one date. Scrolling through, looking for an Image. Hello 14th April
and your 3k Images...

So I'm trying to find a solution to merge these images into iCloud, containing as much info as to save,
timestamped and ordered correctly.

# My solution
Inside the takeout were json files containing timestamps and sometimes GPS info. Some contained neither.
Therefor I'm reading all json files and exif data from jpgs and other file formats supporting exif.
(Is this a jpg/jpeg exclusive feature?)

By merging json data into images containing less info and 
manipulating files creation (mac only currently), access and modified date.

# Issues I encountered
- Getting json file for each Image is pretty annoying due to different naming schemas.
You may improve this to your needs, depending on your naming schema.
- Understanding piexif
- Understanding exif gps format and the conversion from decimal to degree, minutes, seconds.
I tried to do a little manual tests and a unit test to check it converts correctly. No guarantee!
