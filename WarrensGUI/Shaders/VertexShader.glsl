#version 330

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;
layout(location = 2) in vec3 normal;

smooth out vec4 interpColor;

uniform vec3 dirToLight;
uniform vec4 lightIntensity;

uniform mat4 perspectiveMatrix;
uniform mat4 cameraMatrix;
uniform mat3 lightingMatrix;

void main()
{
	gl_Position = perspectiveMatrix * cameraMatrix * position;

	vec3 normCamSpace = normalize(lightingMatrix * normal);
	
	float cosAngIncidence = dot(normCamSpace, dirToLight);
	cosAngIncidence = clamp(cosAngIncidence, 0, 1);
	
	interpColor = lightIntensity * color * cosAngIncidence;
}