from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype("Tests/fonts/CBDTTestFont.ttf", size=64)
im = Image.new("RGB", (128, 96), "white")
d = ImageDraw.Draw(im)
d.text((16, 16), "AB", font=font, embedded_color=True)
print("Log: Script ran successfully")
