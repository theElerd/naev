/*
 * See Licensing and Copyright notice in naev.h
 */
#pragma once

#include "glad.h"

typedef struct mat4_ {
   /* Column-major; m[x][y] */
   GLfloat m[4][4];
} mat4;

/* Basic operations. */
void mat4_print( mat4 m );
void mat4_mul( mat4 *out, const mat4 *m1, const mat4 *m2 );

/* Affine transformations. */
void mat4_scale( mat4 *m, double x, double y, double z );
void mat4_translate( mat4 *m, double x, double y, double z );
void mat4_rotate( mat4 *m, double angle, double x, double y, double z );
void mat4_rotate2d( mat4 *m, double angle );
void mat4_rotate2dv( mat4 *m, double x, double y );
GLfloat *mat4_ptr( mat4 *m );

/* Creation functions. */
__attribute__((const)) mat4 mat4_identity( void );
__attribute__((const)) mat4 mat4_ortho( double left, double right,
                           double bottom, double top, double nearVal, double farVal );

/* TODO move this to opengl place. */
void mat4_uniform( GLint location, mat4 m );
