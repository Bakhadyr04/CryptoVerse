type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  children: React.ReactNode;
};

export function Button({ children, className = "", ...props }: Props) {
  return (
    <button
      className={`px-4 py-2 rounded font-semibold transition ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
