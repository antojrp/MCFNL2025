import numpy as np
import matplotlib.pyplot as plt
import pytest
from fdtd2d import FDTD2D, analytic_chiral_RT, transmission_from_gaussian_pulse
from fdtd1d import gaussian_pulse, C0


def test_fdtd_2d_solver_band_x():
    nx, ny = 101, 101
    xE = np.linspace(-5, 5, nx)
    yE = np.linspace(-5, 5, ny)

    x0, y0 = 0.0, 0.0
    sigma = 0.25

    dx = xE[1] - xE[0]
    dy = yE[1] - yE[0]
    dt = 0.5 * np.sqrt(dx**2 + dy**2) / C0
    Tf = 2

    initial_condition_x = np.zeros((nx, ny))
    for i in range(nx):
        gaussian_value = gaussian_pulse(xE[i], x0, sigma)
        for j in range(ny):
            initial_condition_x[i, j] = gaussian_value

    solver = FDTD2D(xE, yE)
    solver.set_initial_condition(initial_condition_x)
    Hz_final = solver.run_until(Tf, dt)

    mid_y = ny // 2
    section_x = Hz_final[:, mid_y]

    expected_x = \
        0.5 * gaussian_pulse(xE, x0 - C0 * Tf, sigma) + \
        0.5 * gaussian_pulse(xE, x0 + C0 * Tf, sigma)

    assert np.corrcoef(section_x, expected_x)[0, 1] >= 0.99


def test_fdtd_2d_solver_band_y():
    nx, ny = 101, 101
    xE = np.linspace(-5, 5, nx)
    yE = np.linspace(-5, 5, ny)

    x0, y0 = 0.0, 0.0
    sigma = 0.25

    dx = xE[1] - xE[0]
    dy = yE[1] - yE[0]
    dt = 0.5 * np.sqrt(dx**2 + dy**2) / C0
    Tf = 2

    initial_condition_y = np.zeros((nx, ny))
    for j in range(ny):
        gaussian_value = gaussian_pulse(yE[j], y0, sigma)
        for i in range(nx):
            initial_condition_y[i, j] = gaussian_value

    solver = FDTD2D(xE, yE)
    solver.set_initial_condition(initial_condition_y)
    Hz_final_y = solver.run_until(Tf, dt)

    mid_x = nx // 2
    section_y = Hz_final_y[mid_x, :]

    expected_y = 0.5 * gaussian_pulse(yE, y0 - C0 * Tf, sigma) + \
        0.5 * gaussian_pulse(yE, y0 + C0 * Tf, sigma)

    assert np.corrcoef(section_y, expected_y)[0, 1] >= 0.99


def test_fdtd_2d_solver_PML_relection_coefficient():
    nx, ny = 101, 101
    L = 101
    xE = np.linspace(-L/2, L/2, nx)
    yE = np.linspace(-L/2, L/2, ny)

    x0, y0 = 0.0, 0.0
    sigma = 3.0

    dx = xE[1] - xE[0]
    dy = yE[1] - yE[0]
    dt = 0.5 * np.sqrt(dx**2 + dy**2) / C0
    Tf = L

    #PML variables
    R0=1.5e-6 #Reflection admited
    m=2.82 # Steepness of the grading
    thicknessPML=10 # Thickness of the PML in number of cells

    # Set initial conditions to a gaussian pulse in x and y
    initial_condition = np.zeros((nx, ny))
    for i in range(nx):
        for j in range(ny):
            initial_condition[i, j] = gaussian_pulse(xE[i], x0, sigma) * gaussian_pulse(yE[j], y0, sigma)

    solver = FDTD2D(xE, yE)
    solver.set_initial_condition(initial_condition)

    # Save initial Hz field
    initial_Hz = np.max(np.abs(solver.Hz.copy()))

    # Set PML
    solver.set_PML(thicknessPML, m, R0, dx)

    # Run the simulation
    solver.run_until(Tf, dt)

    # Check that the energy after the wave have passed through the PML is almost 0 in the whole grid
    final_Hz = np.max(np.abs(solver.Hz.copy()))

    assert np.abs(final_Hz / initial_Hz)**2 < 0.01


@pytest.mark.skip("Not really a test")
def test_fdtd_2d_solver_gaussian():
    """Test 2D FDTD solver with a 2D Gaussian pulse initial condition."""
    nx, ny = 101, 101
    xE = np.linspace(-5, 5, nx)
    yE = np.linspace(-5, 5, ny)

    x0, y0 = 0.0, 0.0
    sigma = 0.25

    dx = xE[1] - xE[0]
    dy = yE[1] - yE[0]
    dt = 0.5 * np.sqrt(dx**2 + dy**2) / C0
    Tf = 2

    initial_condition = np.zeros((nx, ny))
    for i in range(nx):
        for j in range(ny):
            initial_condition[i, j] = gaussian_pulse(xE[i], x0, sigma) * gaussian_pulse(yE[j], y0, sigma)

    solver = FDTD2D(xE, yE)
    solver.set_initial_condition(initial_condition)
    Hz_final = solver.run_until(Tf, dt)

    mid_x = nx // 2
    mid_y = ny // 2
    section_x = Hz_final[:, mid_y]
    section_y = Hz_final[mid_x, :]

    expected_x = 0.5 * gaussian_pulse(xE, x0 - C0 * Tf, sigma) + \
        0.5 * gaussian_pulse(xE, x0 + C0 * Tf, sigma)
    expected_y = 0.5 * gaussian_pulse(yE, y0 - C0 * Tf, sigma) + \
        0.5 * gaussian_pulse(yE, y0 + C0 * Tf, sigma)

    fig = plt.figure(figsize=(15, 5))
    
    ax1 = plt.subplot(131)
    im1 = ax1.imshow(initial_condition, extent=[yE[0], yE[-1], xE[0], xE[-1]], 
                     aspect='equal', cmap='RdBu', origin='lower')
    plt.colorbar(im1, ax=ax1)
    ax1.set_title('Initial Condition')
    ax1.set_xlabel('y')
    ax1.set_ylabel('x')
    
    ax2 = plt.subplot(132)
    im2 = ax2.imshow(Hz_final, extent=[yE[0], yE[-1], xE[0], xE[-1]], 
                     aspect='equal', cmap='RdBu', origin='lower')
    plt.colorbar(im2, ax=ax2)
    ax2.set_title('Final Condition')
    ax2.set_xlabel('y')
    ax2.set_ylabel('x')
    
    ax3 = plt.subplot(133)
    ax3.plot(xE, section_x, label='Section in X (2D)')
    ax3.plot(xE, expected_x, '--', label='Expected in X (1D)')
    ax3.plot(yE, section_y, label='Section in Y (2D)')
    ax3.plot(yE, expected_y, '--', label='Expected in Y (1D)')
    ax3.set_title('1D Sections')
    ax3.legend()
    ax3.grid(True)
    
    plt.tight_layout()
    plt.show() 

def test_fdtd_2d_solver_chiral_panel():
    # Define the grid
    xE = np.linspace(0, 10, 100)
    yE = np.linspace(0, 10, 100)

    # Create the FDTD2D object
    fdtd = FDTD2D(xE, yE)

    # Set initial condition (Gaussian pulse)
    X, Y = np.meshgrid(xE, yE)
    initial_condition = np.exp(-((X - 5)**2 + (Y - 5)**2) / 0.1)

    fdtd.set_initial_condition(initial_condition)

   # Set PML parameters
    # fdtd.set_PML(thicknessPML=100, m=10, R0=0.001, dx=fdtd.dx)

    # 5) Definir panel quiral 
    λ0 = 0.5
    x0 = 5
    y0 = 3
    wx = 17 * λ0
    wy = 0.3 * λ0
    eps = 1.0
    sigma = 6.0
    kappa = 0.0

    fdtd.E_trans = 0

    fdtd.pos = y0 - wy/2 - fdtd.dy

    # Run the simulation and visualize
    fdtd.simulate_and_plot(Tf=4, dt=0.005, simulate = False)

    E_trans_no_panel = fdtd.aux

    fdtd = FDTD2D(xE, yE)
    fdtd.pos = y0 - wy/2 - fdtd.dy
    fdtd.set_initial_condition(initial_condition)

    fdtd.set_chiral_panel(x0, y0, wx, wy, eps, sigma, kappa)
    fdtd.simulate_and_plot(Tf=4, dt=0.005, simulate = False)

    E_trans_panel = fdtd.aux

    T = abs( E_trans_panel / E_trans_no_panel)
    print(f"Transmisión: {T:.2f}")

    transmission = transmission_from_gaussian_pulse(wy, kappa, sigma, eps_r=1.0, mu_r=1.0, sigma_t=np.sqrt(0.1/2), dt=0.01, N=100)
    print(f"Transmisión nuevo: {transmission:.2f}")

    assert np.abs(T - transmission) <= 0.055, f"Expected {transmission:.4f}, got {T:.4f}"

def test_chirality():
    # Define the grid
    xE = np.linspace(0, 10, 100)
    yE = np.linspace(0, 10, 100)

    # Create the FDTD2D object
    fdtd = FDTD2D(xE, yE)

    # Set initial condition (Gaussian pulse)
    X, Y = np.meshgrid(xE, yE)
    initial_condition = np.exp(-((X - 5)**2 + (Y - 5)**2) / 0.1)

    fdtd.set_initial_condition(initial_condition)

   # Set PML parameters
    # fdtd.set_PML(thicknessPML=100, m=10, R0=0.001, dx=fdtd.dx)

    # 5) Definir panel quiral 
    kappa_medio = 1.0
    fdtd.kappaEy = np.ones((fdtd.nx - 1, fdtd.ny    ))*kappa_medio
    fdtd.kappaEx = np.ones((fdtd.nx, fdtd.ny -1  ))*kappa_medio


    fdtd.simulate_and_plot(Tf=5, dt=0.005, simulate = True)
                               


    

#test_chirality()

test_fdtd_2d_solver_chiral_panel()


'''if __name__ == "__main__":
    pytest.main([__file__])'''


