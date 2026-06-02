import { z } from 'zod';

export const loginSchema = z.object({
    email: z.string().trim().email('Enter a valid email'),
    password: z.string().min(1, 'Password is required'),
});

export type LoginSchema = z.infer<typeof loginSchema>;

export const registerSchema = z
    .object({
        full_name: z.string().trim().optional(),
        email: z.string().trim().email('Enter a valid email'),
        password: z.string().min(8, 'Password must be at least 8 characters'),
        confirmPassword: z.string().min(1, 'Confirm your password'),
    })
    .superRefine((val, ctx) => {
        if (val.password !== val.confirmPassword) {
            ctx.addIssue({
                code: z.ZodIssueCode.custom,
                path: ['confirmPassword'],
                message: 'Passwords do not match',
            });
        }
    });

export type RegisterSchema = z.infer<typeof registerSchema>;

