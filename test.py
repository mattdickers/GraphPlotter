import matplotlib.pyplot as plt

xs = [0,1,2,3,4]
ys = [4,3,2,1,0]

def RGBtoFloat(rgb):
    return (rgb[0]/255, rgb[1]/255, rgb[2]/255)

plt.plot(xs,ys,"-", color=RGBtoFloat((255,0,0)))
plt.show()