import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="text-center py-5">
      <h1 className="h2">Page not found</h1>
      <p>
        <Link to="/">Back to home</Link>
      </p>
    </div>
  );
}
