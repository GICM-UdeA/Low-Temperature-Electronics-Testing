#include <AccelStepper.h>

// Define the motor interface type and pins
#define MOTOR_INTERFACE_TYPE 1 // Use 1 for a single-pin driver (e.g., A4988), 2 for a dual-pin driver (e.g., DRV8825)
#define STEP_PIN 7
#define DIR_PIN 4
#define ENABLE_PIN 8

// Define the steps per revolution and microstepping mode of the driver
#define STEPS_PER_REVOLUTION 200 // Change this value if your motor has a different step count
#define MICROSTEPPING 16 // Change this value to match the microstepping mode of your driver (e.g., 1, 2, 4, 8, 16, etc.)

// Create an instance of the AccelStepper class
AccelStepper stepper(MOTOR_INTERFACE_TYPE, STEP_PIN, DIR_PIN);

// Variable to store the desired distance
float desiredDistance = 0;

// Variable to indicate if the motor should be stopped
volatile bool stopMotorUP = false;
volatile bool stopMotorDOWN = false; 

void setup() {
  // Set up the serial communication
  Serial.begin(115200);

  // Set the maximum speed and acceleration of the motor
  stepper.setMaxSpeed(1000); // Change this value to adjust the maximum speed of the motor
  stepper.setAcceleration(10000); // Change this value to adjust the acceleration of the motor
  
  // Set the D3 (INT1) pin as an input
  pinMode(3, INPUT_PULLUP);
  // Set the D2 (INT0) pin as an input
  pinMode(2, INPUT_PULLUP);
  
  // Attach the interrupt to the D3 (INT1) pin and specify the function to call
  attachInterrupt(digitalPinToInterrupt(3), stopMotorInterruptUP, FALLING);
  // Attach the interrupt to the D2 (INT0) pin and specify the function to call
  attachInterrupt(digitalPinToInterrupt(2), stopMotorInterruptDOWN, FALLING);
}

void loop() {
  // Check if there is data available to read from the serial port
  if (Serial.available() > 0) {
    // Read the entire string until a new line is received
    String input = Serial.readStringUntil('\n');
    input.trim(); // Remove leading/trailing whitespaces

    // Check if the input starts with "M"
    if (input.startsWith("M")) {
      // Convert the input to a float value (excluding the "M" at the beginning)
      desiredDistance = input.substring(1).toFloat();

      Serial.print("Received distance: ");
      Serial.print(desiredDistance);
      Serial.println(" cm");

      // Calculate the direction based on the sign of the desired distance
      int direction = (desiredDistance >= 0) ? 1 : -1;

      // Calculate the number of steps needed to move the desired distance
      float steps = 189.0427018336821 * abs(desiredDistance) + 13.19385226180907; 
      
      // Move the motor to the desired position with the specified direction
      stepper.move(direction * steps);
    }
  }

  // Check if the motor should be stopped
  if (stopMotorUP) {
    // Stop the motor
    stepper.stop();
    //digitalWrite(ENABLE_PIN, HIGH);
    stopMotorUP = false; // Reset the flag
    Serial.println("Motor stopped due to endstop switch.");
    stepper.move(-0.6 * 189.0427018336821 + 13.19385226180907);
  }

  // Check if the motor should be stopped
  if (stopMotorDOWN) {
    // Stop the motor
    stepper.stop();
    //digitalWrite(ENABLE_PIN, HIGH);
    stopMotorDOWN = false; // Reset the flag
    Serial.println("Motor stopped due to endstop switch.");
    stepper.move(0.6 * 189.0427018336821 + 13.19385226180907);
  }

  // Run the stepper motor
  //digitalWrite(ENABLE_PIN, LOW);
  stepper.run();

  // Check if the motor has reached the desired position
  if (stepper.distanceToGo() == 0 && desiredDistance != 0) {
    // Motor has reached the desired position
    // You can add any additional code here to perform actions after the motor movement is complete
    Serial.println("Motor movement complete");
    desiredDistance = 0; // Reset the desired distance
  }
}

// Interrupt service routine to stop the motor
void stopMotorInterruptUP() {
  stopMotorUP = true;
}

// Interrupt service routine to stop the motor
void stopMotorInterruptDOWN() {
  stopMotorDOWN = true;
}
