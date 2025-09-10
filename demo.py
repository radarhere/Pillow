from PIL import Image, ImageDraw, ImageFont

def convert_emoji_to_png(emoji):
    image_size = (64, 64) # set image size
    image = Image.new("RGBA", image_size, (0, 0, 0, 0))  # Set transparent background
    font_size = 64  # Adjusted font size
    font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"
    font = ImageFont.truetype(font_path, font_size, encoding='unic')
    draw_position = (int((image_size[0] - font_size) / 2), int((image_size[1] - font_size) / 2))
    draw = ImageDraw.Draw(image)
    draw.text(draw_position, emoji, font=font, embedded_color=True)
    image.save("out.png")

convert_emoji_to_png("👩‍🦽‍➡️")
