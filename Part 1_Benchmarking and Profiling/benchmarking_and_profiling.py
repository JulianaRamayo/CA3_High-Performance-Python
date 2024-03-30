import time
from PIL import Image
import array
from functools import wraps

def timefn(fn):
    @wraps(fn)
    def measure_time(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        print("@timefn:" + fn.__name__ + " took " + str(end - start) + " seconds")
        return result
    return measure_time

# Example 2-1. Defining global constants for the coordinate space
'''Julia set generator without optional PIL-based image drawing'''
# area of complex space to investigate
x1, x2, y1, y2 = -1.8, 1.8, -1.8, 1.8
c_real, c_imag = -0.62772, -.42193

# Example 2-2. stablishing the coordinate lists as inputs to our
# calculation function
@profile
def calc_pure_python(desired_width, max_iterations, return_output=False):
    '''Create a list of complex coordinates (zc) and complex
    parameters (cs), build Julia set, and display'''
    x_step = (float(x2 - x1) / float(desired_width))
    y_step = (float(y1 - y2) / float(desired_width))
    x = []
    y = []
    ycoord = y2
    while ycoord > y1:
        y.append(ycoord)
        ycoord += y_step
    xcoord = x1
    while xcoord < x2:
        x.append(xcoord)
        xcoord += x_step
    # Build a list of coordinates and the initial condition for each cell.
    # Note that our initial condition is a constant and could easily be removed;
    # we use it to simulate a real-world scenario with several inputs to
    # our function.
    zs = []
    cs = []
    for ycoord in y:
        for xcoord in x:
            zs.append(complex(xcoord, ycoord))
            cs.append(complex(c_real, c_imag))
    
    print("Lenght of x:", len(x))
    print("Total elements:", len(zs))
    start_time = time.time()
    output = calculate_z_serial_purepython(max_iterations, zs, cs)
    end_time = time.time()
    secs = end_time - start_time
    print(calculate_z_serial_purepython.__name__ + " took", secs, "seconds")
    
    # This sum is expected for a 1000^2 grid with 300 iterations.
    # It catches minor errors we might introduce when we're
    # working on a fixed set of inputs.
    assert sum(output) == 33219980
    if return_output:
        return output
    
# Example 2-3. Our CPU-bound calculation function
@timefn
@profile
def calculate_z_serial_purepython(maxiter, zs, cs):
    '''Calculate output list using Julia update rule'''
    output = [0] * len(zs)
    for i in range(len(zs)):
        n = 0
        z = zs[i]
        c = cs[i]
        while abs(z) < 2 and n < maxiter:
            z = z * z + c
            n += 1
        output[i] = n
    return output

def false_grayscale(desired_width, max_iterations):
    # Calculate the Julia set
    output = calc_pure_python(desired_width, max_iterations, return_output=True)
    
    # Find the maximum iteration value for normalization
    max_value = float(max(output))
    
    # Normalize iteration counts to the 0-255 grayscale range.
    output_raw_limited = [int(float(o) / max_value * 255) for o in output]
    
    # Convert grayscale values to equivalent RGB values.
    # Since the image is grayscale, R, G, and B components are the same.
    # Each value in the generator will be a 32-bit integer where the least significant
    # 24 bits are R, G, and B values (all three are the same for grayscale),
    # multiplied by 16 to fill the 32 bits (since we're ignoring the alpha channel).
    output_rgb = ((o + (256 * o) + (256 ** 2) * o) * 16 for o in output_raw_limited)
    
    # Convert the RGB generator to an array of unsigned integers ('I').
    output_rgb = array.array('I', output_rgb)
    
    # Create a new RGB image with the desired dimensions.
    img = Image.new("RGB", (desired_width, desired_width))
    img.frombytes(output_rgb.tobytes(), "raw", "RGBX", 0, -1)
    img.show()

def pure_grayscale(desired_width, max_iterations):
    output = calc_pure_python(desired_width, max_iterations, return_output=True)
    
    # Maximum iteration count as the scale factor for normalization.
    scale_factor = float(max(output))
    
    # Normalize the iteration counts to the 0-255 grayscale range.
    # Values are scaled linearly based on the maximum number of iterations.
    # The result is a pure grayscale value, meaning each pixel's color intensity
    # directly reflects the number of iterations.
    scaled = [int(o / scale_factor * 255) for o in output]
    
    # Convert the scaled iteration counts into an array of unsigned bytes ('B').
    # Each byte represents a pixel's grayscale color value in the image.
    output = array.array('B', scaled)
    
    # Create a new grayscale image.
    img = Image.new("L", (desired_width, desired_width))
    img.frombytes(output.tobytes(), "raw", "L", 0, -1)
    img.show()

if __name__ == "__main__":
    # Calculate the Julia set using a pure Python solution with
    # reasonable defaults for a laptop
    calc_pure_python(desired_width=1000, max_iterations=300)
