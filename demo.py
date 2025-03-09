import PIL.Image
import PIL.ImageFilter
version = PIL.Image.__version__
print(version)

i = PIL.Image.open("pelican-bird.png")
i.filter(PIL.ImageFilter.SMOOTH_MORE)
i.save("smooth_more_result"+str(version)+".png")

comparison = PIL.Image.open("smooth_more_result10.2.0.png")
assert comparison.tobytes() == i.tobytes()

i.filter(PIL.ImageFilter.DETAIL)
i.save("detail_result"+str(version)+".png")

comparison = PIL.Image.open("detail_result10.2.0.png")
assert comparison.tobytes() == i.tobytes()
