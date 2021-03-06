#version 330

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;
layout(location = 2) in vec3 normal;

smooth out vec4 interpColor;

// Camera & Perspective projection
uniform mat4 perspectiveMatrix;
uniform mat4 cameraMatrix;

// Lighting inputs
uniform vec3 lightPos;
uniform vec4 lightIntensity;
uniform vec4 ambientIntensity;
uniform mat3 lightingMatrix;

// Fog of war inputs
uniform vec4 playerPosition;
uniform float fogDistance;
uniform bool fogActive;

void main()
{
	// Calculate the gl_Position for the vertex position
	// Attention the same formula has to be set in the python
	// code where normalized device coordinates are calculated.
	vec4 camSpacePosition = cameraMatrix * position;
	gl_Position = perspectiveMatrix * camSpacePosition;

	vec3 camSpaceNormal = normalize(lightingMatrix * normal);

    vec3 camSpaceLightPos = lightingMatrix * lightPos;

	vec3 dirToLight = normalize(camSpaceLightPos - vec3(camSpacePosition));

	float cosAngIncidence = dot(camSpaceNormal, dirToLight);
	cosAngIncidence = clamp(cosAngIncidence, 0, 1);

    // Color coming from direct light
	vec4 directLightColor = color * lightIntensity * cosAngIncidence;

	// Color coming from ambient light
	vec4 ambientLightColor = color * ambientIntensity;

    // Fog of war
    interpColor = directLightColor + ambientLightColor;
    if ( fogActive == true)
    {
        float myDist = distance(playerPosition, position);
        float fullViewDist = fogDistance * 0.75;
        float minimumClarity = 0.25;
        if ( myDist <= fullViewDist )
        {
            //100% clarity
            interpColor = directLightColor + ambientLightColor;
        }
        else if ( myDist <= fogDistance )
        {
            //100% to 20% clarity
            float gradient = 1 - ((myDist - fullViewDist) / (fogDistance - fullViewDist));
            gradient = clamp(gradient, minimumClarity , 1.0);
            interpColor = (directLightColor + ambientLightColor) * gradient;
            interpColor[3] = 1.0;
            //Note: This probably messes up transparency in the edge of the Fog
        }
        else
        {
            //20% clarity
            float gradient = minimumClarity;
            interpColor = (directLightColor + ambientLightColor) * gradient;
            interpColor[3] = 1.0;
            //Full black
            //interpColor = vec4(0.0, 0.0, 0.0, 1.0);
        }
    }

	// Make sure final output is in [0:1]
	interpColor = clamp(interpColor, 0, 1);
}
