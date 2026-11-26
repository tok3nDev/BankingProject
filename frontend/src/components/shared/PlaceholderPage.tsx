interface PlaceholderPageProps {
  title: string;
}

export function PlaceholderPage({ title }: PlaceholderPageProps) {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-text-primary">
        {title}
      </h1>
      <p className="mt-2 text-sm text-text-secondary">
        This section is under development.
      </p>
    </div>
  );
}