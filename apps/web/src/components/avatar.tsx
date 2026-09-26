import Image from "next/image";

export function Avatar({
  name,
  src,
  size = "md",
}: {
  name: string;
  src?: string | null;
  size?: "sm" | "md" | "lg";
}) {
  const pixels = size === "lg" ? 96 : size === "md" ? 44 : 32;
  if (src) {
    return (
      <Image
        className={`avatar avatar-${size}`}
        src={src}
        alt={`${name}'s avatar`}
        width={pixels}
        height={pixels}
        unoptimized
      />
    );
  }
  return (
    <span className={`avatar avatar-${size} avatar-fallback`} aria-label={`${name}'s avatar`}>
      {name.slice(0, 1).toUpperCase()}
    </span>
  );
}
