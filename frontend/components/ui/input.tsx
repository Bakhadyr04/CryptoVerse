type Props = React.InputHTMLAttributes<HTMLInputElement>;

export function Input({ className = "", ...props }: Props) {
  return (
    <input
      className={`px-3 py-2 rounded bg-white text-black ${className}`}
      {...props}
    />
  );
}
