#version 330

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;
layout(location = 2) in vec3 normal;

smooth out vec4 interpColor;

// Camera & Perspective projection
uniform mat4 perspectiveMatrix;
uniform mat4 cameraMatrix;

// Lighting inputs
uniform vec3 dirToLight;
uniform vec4 lightIntensity;
uniform vec4 ambientIntensity;
uniform mat3 lightingMatrix;

// Fog of war inputs
uniform vec4 playerPosition;
uniform float fogDistance;

void main()
{
	gl_Position = perspectiveMatrix * cameraMatrix * position;

	vec3 normCamSpace = normalize(lightingMatrix * normal);
	
	float cosAngIncidence = dot(normCamSpace, dirToLight);
	cosAngIncidence = clamp(cosAngIncidence, 0, 1);

    // Color coming from direct light
	vec4 directLightColor = lightIntensity * color * cosAngIncidence;

	// Color coming from ambient light
	vec4 ambientLightColor = ambientIntensity * color;

    // Fog of war
    //vec4 playerPosition = vec4(1.0, 1.0, 1.0, 1.0);
    float myDist = distance(playerPosition, position);
    float fullViewDist = fogDistance / 3;
    if ( myDist <= fullViewDist )
    {
	    interpColor = directLightColor + ambientLightColor;
	}
	else if ( myDist <= fogDistance )
	{
	    float gradient = 1 - ((myDist - fullViewDist) / (fogDistance - fullViewDist));
	    interpColor = (directLightColor + ambientLightColor) * gradient;
	    interpColor[3] = 1.0;
	}
	else
	{
	    interpColor = vec4(0.0, 0.0, 0.0, 1.0);
	}

	// Make sure final output is in [0:1]
	interpColor = clamp(interpColor, 0, 1);
}