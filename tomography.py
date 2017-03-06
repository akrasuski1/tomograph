from PIL import Image, ImageDraw
import math

def generate_beams(n_emitters, l_spread, w, alpha):
    p1=[]
    p2=[]
    for j in range(n_emitters):
        d=l_spread*w*(-0.5+j/(n_emitters-1.0))
        x=d
        y=math.sqrt(w*w/4.0-d*d)
        x, y = (x*math.cos(alpha)-y*math.sin(alpha),
                x*math.sin(alpha)+y*math.cos(alpha))
        x+=w/2.0
        y+=w/2.0
        x=int(math.floor(x))
        y=int(math.floor(y))
        p1.append((x, y))
        p2.append((w-1-x, w-1-y))
    return zip(p1, p2[::-1])

def update_sinogram(im, sino, q1, q2, i, j):
    # Not using Bresenham! It's wrong!
    w=im.size[0]
    sm=0
    d=int(((q2[0]-q1[0])**2+(q2[1]-q1[1])**2)**0.5)
    data=im.getdata()
    for k in range(d):
        x=int(q1[0]+(q2[0]-q1[0])*float(k)/d)
        y=int(q1[1]+(q2[1]-q1[1])*float(k)/d)
        sm+=data[y*w+x]
    pix=sm/w # Normalization - max would be 255*w, but we divide by w.
    sino.putpixel((i, j), pix)

# Using parallel tomograph.
def make_sinogram_from_image(img_name, simg_dir, scan_dir, 
        n_samples=100,
        n_emitters=30,
        l_spread=0.5): # Ratio of detector spread to circle diameter
    im=Image.open(img_name).convert("L")
    w, h = im.size
    assert w==h

    sino=Image.new("L", (n_samples, n_emitters))
    for i in range(n_samples):
        print i,"/",n_samples
        sim=im.copy().convert("RGB")
        alpha=math.pi/n_samples*i
        beams=generate_beams(n_emitters, l_spread, w, alpha)
        for j, (q1, q2) in enumerate(beams):
            draw=ImageDraw.Draw(sim)
            x1, y1=q1[0], q1[1]
            x2, y2=q2[0], q2[1]
            draw.ellipse((x1-2, y1-2, x1+2, y1+2), fill=(255, 0, 0))
            draw.ellipse((x2-2, y2-2, x2+2, y2+2), fill=(255, 0, 0))
            draw.line((x1, y1, x2, y2), fill=(128, 0, 0))

            update_sinogram(im, sino, q1, q2, i, j)
        sim.save(scan_dir+"/"+str(i)+".png")
        sino.save(sinogram_dir+"/"+str(i)+".png")

if __name__=="__main__":
    import sys
    input_image=sys.argv[1]
    sinogram_dir=sys.argv[2]
    scan_dir=sys.argv[3]
    make_sinogram_from_image(input_image, sinogram_dir, scan_dir)
