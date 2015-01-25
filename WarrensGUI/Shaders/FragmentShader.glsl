#version 330
//Fragment shader

smooth in vec4 theColor;

out vec4 outputColor;

void main()
{
	outputColor = theColor;
}
