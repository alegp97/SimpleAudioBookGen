from PIL import Image, ImageDraw, ImageFont

img = Image.new('RGB', (256, 256), color = (73, 109, 137))
d = ImageDraw.Draw(img)
# Simple placeholder icon
d.text((80,100), "SABG", fill=(255,255,0))
img.save('c:\\Users\\EM2024007301\\Desktop\\AudioBookGen\\icon.ico')
print("Icon generated.")
