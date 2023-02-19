import json
import pennylane as qml
import pennylane.numpy as np

def create_Hamiltonian(h):
    """
    Function in charge of generating the Hamiltonian of the statement.

    Args:
        h (float): magnetic field strength

    Returns:
        (qml.Hamiltonian): Hamiltonian of the statement associated to h
    """
    coeffs = []
    observables = []

    for i in range(4):
        if i != 3:
            j = i + 1
        else:
            j = 0
        coeffs.append(-1)
        observables.append(qml.PauliZ(wires=[i]) @ qml.PauliZ(wires=[j]))

    for k in range(4):
        coeffs.append(-h)
        observables.append(qml.PauliX(wires=[k]))

    return qml.Hamiltonian(coeffs, observables)

dev = qml.device("default.qubit", wires=4)

@qml.qnode(dev)
def model(params, H):
    """
    To implement VQE you need an ansatz for the candidate ground state!
    Define here the VQE ansatz in terms of some parameters (params) that
    create the candidate ground state. These parameters will
    be optimized later.

    Args:
        params (numpy.array): parameters to be used in the variational circuit
        H (qml.Hamiltonian): Hamiltonian used to calculate the expected value

    Returns:
        (float): Expected value with respect to the Hamiltonian H
    """
    for w in range(4):
        qml.RX(params[w * 2], wires=w)
        qml.RZ(params[w * 2 + 1], wires=w)

    return qml.expval(H)


def train(h):
    """
    In this function you must design a subroutine that returns the
    parameters that best approximate the ground state.

    Args:
        h (float): magnetic field strength

    Returns:
        (numpy.array): parameters that best approximate the ground state.
    """


    def cost(params):
        """Define a cost function that only depends on params, given alpha and beta fixed"""

        return model(params, create_Hamiltonian(h))

    #Initialize parameters, choose an optimization method and number of steps
    init_params = np.array([0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2], requires_grad=True)
    opt = qml.AdamOptimizer(stepsize=0.1)
    steps = 100

    # set the initial parameter values
    params = init_params

    for i in range(steps):
        # update the circuit parameters

        params = opt.step(cost, params)

    return params


# These functions are responsible for testing the solution.
def run(test_case_input: str) -> str:
    ins = json.loads(test_case_input)
    params = train(ins)
    return str(model(params, create_Hamiltonian(ins)))


def check(solution_output: str, expected_output: str) -> None:
    solution_output = json.loads(solution_output)
    expected_output = json.loads(expected_output)
    assert np.allclose(
        solution_output, expected_output, rtol=1e-1
    ), "The expected value is not correct."


test_cases = [['1.0', '-5.226251859505506'], ['2.3', '-9.66382463698038']]

for i, (input_, expected_output) in enumerate(test_cases):
    print(f"Running test case {i} with input '{input_}'...")

    try:
        output = run(input_)

    except Exception as exc:
        print(f"Runtime Error. {exc}")

    else:
        if message := check(output, expected_output):
            print(f"Wrong Answer. Have: '{output}'. Want: '{expected_output}'.")

        else:
            print("Correct!")