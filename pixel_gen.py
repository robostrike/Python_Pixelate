import os
from PIL import Image
import numpy as np
import math as ma
import operator as op

# Predefined list of colors to compare against (as RGBA tuples)
color_list = [
    (255, 0, 0, 255),    # Red
    (0, 255, 0, 255),    # Green
    (0, 0, 255, 255),    # Blue
    (255, 255, 0, 255),  # Yellow
    (255, 255, 255, 255) # White
]

path = os.getcwd()
get_folder = path + "\\pixel_gen"
out_folder = path + "\\result"
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

if not os.path.exists(get_folder):
    os.makedirs(get_folder)
    print("Please add items into the PIXEL_GEN folder")
    exit()


def sharpest_color(block):
    # Convert block to grayscale to calculate intensity differences
    grayscale_block = block.convert('L')  # 'L' mode is for grayscale
    np_block = np.array(grayscale_block)
    
    # Apply edge detection by calculating the gradient (difference between adjacent pixels)
    # Compute the differences between adjacent pixels (horizontal and vertical)
    edges_x = np.abs(np.diff(np_block, axis=0))  # Vertical differences
    edges_y = np.abs(np.diff(np_block, axis=1))  # Horizontal differences
    
    # Ensure edges_x and edges_y are the same size by trimming them to the smallest common shape
    min_shape = (min(edges_x.shape[0], edges_y.shape[0]), min(edges_x.shape[1], edges_y.shape[1]))
    edges_x = edges_x[:min_shape[0], :min_shape[1]]
    edges_y = edges_y[:min_shape[0], :min_shape[1]]
    
    # Combine the two gradient arrays to get the total edge intensity
    edges = edges_x + edges_y
    
    # Find the coordinates of the pixel with the maximum edge intensity
    max_pos = np.unravel_index(np.argmax(edges), edges.shape)
    
    # Get the RGB value of the corresponding pixel in the original block
    sharpest_pixel = block.getpixel((max_pos[1], max_pos[0]))  # (x, y) in original block
    
    return sharpest_pixel

def average_color(block):
    # Convert block (a small image region) to a numpy array
    np_block = np.array(block)
    # Calculate the mean color of the block along the axis for RGB values
    avg_color = np.mean(np_block, axis=(0, 1)).astype(int)
    
    #gradient the color so that it's reduced at intervals of 25
    for i in range(len(avg_color)):
        avg_color[i] = int(ma.floor(avg_color[i]/color_tol)*color_tol)
    
    return tuple(avg_color)

# Function to calculate the Euclidean distance between two colors
def color_distance(c1, c2):
    # Remove the alpha channel if present
    if len(c1) == 4:
        c1 = c1[:3]  # Take only RGB values
    if len(c2) == 4:
        c2 = c2[:3]  # Take only RGB values

    # Calculate Euclidean distance in RGB space
    return np.sqrt(np.sum((np.array(c1) - np.array(c2))**2))

# Function to find the closest color from a predefined list
def closest_color(pixel_color, color_list):
    closest = color_list[0]
    min_dist = color_distance(pixel_color, closest)
    
    for color in color_list[1:]:
        dist = color_distance(pixel_color, color)
        if dist < min_dist:
            min_dist = dist
            closest = color
    
    return closest

#checking instance of color checking
div_x = 1
div_y = 1
block_size = 20
pixel_size = 10  # Adjust as necessary to increase pixel size
color_tol = 50

initial = 15 #setting the initial size reduction value
check = 0 #counting for file output


output_iden = 1
horizontal_offset = 0
vertical_offset = 0
max_x = 1000
max_y = 1000
local_y = 0

#fit everything in here.
export_img = Image.new('RGB',(max_x,max_y))


items = os.listdir(get_folder)
def export_file(out_num):
# Save the final combined image
        out_file = out_folder + "\\" + item[0:-4] + "_combined" + str(out_num)+ ending
        out_file2 = out_folder + "\\" + item[0:-4] + "_combined" + str(out_num)+ ending
        print("Final combined image saved to:", out_file2)
        #combined_image.save(out_file)
        export_img.save(out_file2)
        return out_num + 1

for item in items:
    new_width = 0
    
    # To calculate total height for the combined image
    total_height = 0
    
    #check if file is an image to proceed
    if item.lower().endswith(".png") or item.lower().endswith(".jpg"):
        flip = 0 #move the image to the right or down depending on which direction.
        
        ending = item.lower()[-4:]
        file = get_folder + "\\" + item
        img = Image.open(file).convert('RGB')
        print("opening: " + file)

        # Get the width and height of the image
        width, height = img.size

        # Initialize value for `i`
        i = initial  # Start with `i = 2`

        

        # Precalculate the total height needed for all iterations
        iteration_sizes = []
        local_width = ma.ceil(width/i)
        local_height = ma.ceil(height/i*1.75)
        while i <= width:
            new_width = ma.ceil(width / i)
            new_height = ma.ceil(height / i)
            iteration_sizes.append((new_width,new_height))
            i *= 2  # Double the value of `i` for the next iteration
        if local_height > local_y:
            #replace currently most suitable height value reference.
            local_y = local_height
        
        
        #print("Check: ", horizontal_offset + new_width, vertical_offset + local_height, local_y)
        
        # Create a blank image that will fit all iterations stacked vertically and horizontally
        #combined_image = Image.new('RGB', (horizontal_offset + new_width, total_height))
        
        #check if file will burst out of the value on new_width / new_height
        if horizontal_offset + new_width >= max_x:
            #reset the y position and increase from previous max y value
            horizontal_offset = 0
            vertical_offset = vertical_offset + local_y
            
            if vertical_offset > max_y:
                #if vertical is going to go off screen, then need to start new page
                output_iden = export_file(output_iden)
                export_img = Image.new('RGB',(max_x,max_y))
                vertical_offset = 0 #fresh new file
            
            #reset the local height
            local_y = local_height
        if vertical_offset + local_y> max_y: #not influenced by vertical
            #if vertical is going to go off screen, then need to start new page
            output_iden = export_file(output_iden)
            export_img = Image.new('RGB',(max_x,max_y))
            
            vertical_offset = 0 #fresh new file
            horizontal_offset = 0
            
        
        # Reset `i` for the iteration loop and the vertical offset for placing images
        i = initial
        vertical_local = 0  # This will keep track of where to paste the next image
        horizontal_local = 0
        # Now loop through and process the images as before, but combine them
        for new_width, new_height in iteration_sizes:
            # Create a new blank image with the resized dimensions
            new_img = Image.new('RGB', (new_width, new_height))
            
            scale_factor = 1  # Adjust this as needed
            for x in range(0, new_width, scale_factor):  # Move through the width in steps of `scale_factor`
                for y in range(0, new_height, scale_factor):  # Move through the height in steps of `scale_factor`
                    new_width = ma.ceil(width / i)
                    new_height = ma.ceil(height / i)
                    
                    # Define the area for the current pixel block
                    box = (x * i, y * i, (x + 1) * i, (y + 1) * i)
                    
                    # Extract the pixel block from the original image
                    block = img.crop(box)
                    
                    # Get the sharpest color of the pixel block
                    sharpest_color_block = sharpest_color(block)
                    
                    # Create a solid block of the closest color
                    avg_color_block = Image.new('RGB', (1, 1), sharpest_color_block)
                    
                    # Paste the block back into the new image
                    new_img.paste(avg_color_block, (x, y))
                    

            # Paste the current iteration's image into the combined image
            #combined_image.paste(new_img, (horizontal_offset, vertical_offset))
            export_img.paste(new_img,(horizontal_offset+horizontal_local,vertical_offset+vertical_local))
            #print("pasting",horizontal_offset+horizontal_local,vertical_offset+vertical_local)
            
            #alternate so that way it can be possible to shift and save more space
            if flip == 0:
                vertical_local += new_height
            else:
                horizontal_local += new_width
            flip = (flip-1)*-1
            
            # Double the value of `i` for the next iteration
            i *= 2
        
        #shift horizontal after each sequence
        horizontal_offset += local_width
        
    

#print("Final: ", horizontal_offset, vertical_offset, output_iden)
if horizontal_offset >0 or vertical_offset>0:
    #at least one file is out but not stored
    output_iden = export_file(output_iden)
