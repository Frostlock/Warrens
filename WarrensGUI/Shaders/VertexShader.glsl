#version 330
//Vertex Shader

layout (location = 0) in vec4 position;
layout (location = 1) in vec4 color;

uniform mat4 perspectiveMatrix;
uniform mat4 cameraMatrix;

smooth out vec4 theColor;

void main()
{
	gl_Position = perspectiveMatrix * cameraMatrix * position;
	theColor = color;
}
