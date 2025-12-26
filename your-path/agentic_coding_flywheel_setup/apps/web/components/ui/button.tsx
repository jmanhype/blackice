"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { m, type HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";
import { springs } from "@/components/motion";

/**
 * Button variants with Apple HIG compliant sizing:
 * - default: 44px (minimum touch target)
 * - sm: 36px (for compact contexts)
 * - lg: 48px (comfortable touch)
 * - xl: 56px (hero CTAs)
 */
const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl text-sm font-medium transition-colors disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-md shadow-primary/20 hover:bg-primary/90 active:bg-primary/85",
        destructive:
          "bg-destructive text-white shadow-md shadow-destructive/20 hover:bg-destructive/90 active:bg-destructive/85",
        outline:
          "border-2 border-border bg-transparent hover:bg-accent/10 hover:border-accent/50 active:bg-accent/20",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80 active:bg-secondary/70",
        ghost:
          "hover:bg-accent/20 hover:text-accent-foreground active:bg-accent/30",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-11 px-5 py-2.5 text-sm",
        sm: "h-9 px-4 text-sm rounded-lg",
        lg: "h-12 px-6 text-base rounded-xl",
        xl: "h-14 px-8 text-lg rounded-xl",
        icon: "size-11 rounded-xl",
        "icon-sm": "size-9 rounded-lg",
        "icon-lg": "size-12 rounded-xl",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

type ButtonVariantProps = VariantProps<typeof buttonVariants>;

interface ButtonProps
  extends Omit<HTMLMotionProps<"button">, "children">,
    ButtonVariantProps {
  asChild?: boolean;
  children?: React.ReactNode;
  /** Disable motion animations (for server components or reduced motion) */
  disableMotion?: boolean;
}

/**
 * Button component with spring animations and HIG-compliant touch targets.
 *
 * Features:
 * - 44px minimum height (default) for reliable touch targets
 * - Spring-based hover and tap animations
 * - Multiple variants: default, destructive, outline, secondary, ghost, link
 * - Multiple sizes: sm (36px), default (44px), lg (48px), xl (56px)
 * - Icon-only variants with square proportions
 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "default",
      size = "default",
      asChild = false,
      disableMotion = false,
      children,
      ...props
    },
    ref
  ) => {
    // For asChild, use Slot without motion
    if (asChild) {
      return (
        <Slot
          ref={ref as React.Ref<HTMLElement>}
          className={cn(buttonVariants({ variant, size, className }))}
          {...(props as React.ComponentPropsWithoutRef<typeof Slot>)}
        >
          {children}
        </Slot>
      );
    }

    // For link variant or disableMotion, render without animations
    if (variant === "link" || disableMotion) {
      return (
        <button
          type="button"
          ref={ref}
          className={cn(buttonVariants({ variant, size, className }))}
          {...(props as React.ComponentPropsWithoutRef<"button">)}
        >
          {children}
        </button>
      );
    }

    // Motion-enhanced button with spring animations
    // Using m.button (not motion.button) for LazyMotion compatibility
    return (
      <m.button
        type="button"
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        transition={springs.snappy}
        {...props}
      >
        {children}
      </m.button>
    );
  }
);

Button.displayName = "Button";

export { Button, buttonVariants };
