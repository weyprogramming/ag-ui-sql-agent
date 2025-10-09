'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

import {
  accesifyClient,
  type SqlDependencyCreateRequest,
  type SqlDependencyModel,
} from "@/sdk";

const typeOptions: SqlDependencyCreateRequest["type"][] = [
  "sqlite",
  "postgres",
  "mysql",
  "mssql",
];

const createDefaultForm = (): SqlDependencyCreateRequest => ({
  type: "mssql",
  name: "",
  host: "",
  port: 1433,
  database: "",
  username: "",
  password: "",
});

const getDependencyKey = (dependency: SqlDependencyModel): string =>
  dependency.pk ?? dependency.name;

interface CreateSqlDependencyButtonProps {
  onSelect?: (dependency: SqlDependencyModel | null) => void;
}

export default function CreateSqlDependencyButton({
  onSelect,
}: CreateSqlDependencyButtonProps) {
  const onSelectRef = useRef(onSelect);
  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);

  const [isOpen, setIsOpen] = useState(false);
  const [formState, setFormState] = useState<SqlDependencyCreateRequest>(
    createDefaultForm()
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [dependencies, setDependencies] = useState<SqlDependencyModel[]>([]);
  const [selectedKey, setSelectedKey] = useState<string>("");
  const [isLoadingDependencies, setIsLoadingDependencies] = useState(false);
  const [dependenciesError, setDependenciesError] = useState<string | null>(
    null
  );

  const requiredFields = useMemo(
    () => ["name", "host", "database", "username", "password"] as const,
    []
  );



  const handleFieldChange = <K extends keyof SqlDependencyCreateRequest>(
    field: K,
    rawValue: string
  ) => {
    setFormState((previous) => {
      if (field === "port") {
        const parsed = Number.parseInt(rawValue, 10);
        return {
          ...previous,
          port: Number.isNaN(parsed) ? 0 : parsed,
        };
      }

      if (field === "type") {
        return {
          ...previous,
          type: rawValue as SqlDependencyCreateRequest["type"],
        };
      }

      return {
        ...previous,
        [field]: rawValue,
      } as SqlDependencyCreateRequest;
    });
  };

  const resetForm = () => {
    setFormState(createDefaultForm());
  };

  const validateForm = (state: SqlDependencyCreateRequest): string | null => {
    const missing = requiredFields.filter(
      (field) => !String(state[field]).trim().length
    );

    if (missing.length) {
      return `Please provide values for: ${missing.join(", ")}.`;
    }

    if (!Number.isInteger(state.port) || state.port <= 0) {
      return "Port must be a positive integer.";
    }

    return null;
  };

  const updateSelection = useCallback(
    (list: SqlDependencyModel[], preferredKey?: string | null) => {
      if (!list.length) {
        setSelectedKey("");
        onSelectRef.current?.(null);
        return;
      }

      const normalizedPreferred = preferredKey ?? selectedKey;
      const fallbackKey = getDependencyKey(list[0]);
      const nextKey = list.some(
        (dependency) => getDependencyKey(dependency) === normalizedPreferred
      )
        ? (normalizedPreferred as string)
        : fallbackKey;

      setSelectedKey(nextKey);

      const match = list.find(
        (dependency) => getDependencyKey(dependency) === nextKey
      );
      onSelectRef.current?.(match ?? null);
    },
    [selectedKey]
  );

  const fetchDependencies = useCallback(
    async (preferredKey?: string | null) => {
      setIsLoadingDependencies(true);
      setDependenciesError(null);
      try {
        const list = await accesifyClient.getSqlDependencies();
        setDependencies(list);
        updateSelection(list, preferredKey);
        return list;
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Failed to load dependencies.";
        setDependenciesError(message);
        setDependencies([]);
        setSelectedKey("");
        onSelectRef.current?.(null);
        return [];
      } finally {
        setIsLoadingDependencies(false);
      }
    },
    [updateSelection]
  );

  useEffect(() => {
    void fetchDependencies();
  }, [fetchDependencies]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitError(null);

    const validationError = validateForm(formState);
    if (validationError) {
      setSubmitError(validationError);
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await accesifyClient.createSqlDependency(formState);
      setSuccessMessage(`Created SQL dependency "${response.name}".`);
      resetForm();
      setIsOpen(false);
      await fetchDependencies(getDependencyKey(response));
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Failed to create dependency.";
      setSubmitError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOpen = () => {
    setSubmitError(null);
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
  };

  const handleSelectChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const nextKey = event.target.value;
    setSelectedKey(nextKey);
    const match = dependencies.find(
      (dependency) => getDependencyKey(dependency) === nextKey
    );
    onSelectRef.current?.(match ?? null);
  };

  return (
    <section className="rounded-lg border border-gray-200 bg-gray-50 p-4 shadow-sm">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">SQL Dependencies</h2>
          <p className="text-sm text-gray-600">
            Register or choose a database connection for the agent.
          </p>
        </div>
        <button
          type="button"
          onClick={handleOpen}
          className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
        >
          New SQL Dependency
        </button>
      </header>

      <div className="mt-4 space-y-4">
        {isLoadingDependencies && (
          <p className="text-sm text-gray-500">Loading dependencies…</p>
        )}

        {dependenciesError && (
          <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            <div className="flex items-start justify-between gap-4">
              <span>{dependenciesError}</span>
              <button
                type="button"
                onClick={() => void fetchDependencies()}
                className="rounded-md border border-red-300 px-2 py-1 text-xs font-semibold text-red-700 hover:bg-red-100"
              >
                Retry
              </button>
            </div>
          </div>
        )}

  {!isLoadingDependencies && !dependenciesError && (
          <div className="space-y-2">
            <label className="flex flex-col gap-2">
              <span className="text-sm font-medium text-gray-700">
                Choose an existing dependency
              </span>
              {dependencies.length ? (
                <select
                  value={selectedKey}
                  onChange={handleSelectChange}
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {dependencies.map((dependency) => (
                    <option
                      key={getDependencyKey(dependency)}
                      value={getDependencyKey(dependency)}
                    >
                      {dependency.name}
                    </option>
                  ))}
                </select>
              ) : (
                <p className="text-sm text-gray-500">
                  No dependencies registered yet. Create one to get started.
                </p>
              )}
            </label>

            {dependencies.length > 0 && selectedKey ? (
              <div className="rounded-md border border-gray-200 bg-white p-3 text-sm text-gray-700">
                {(() => {
                  const selected = dependencies.find(
                    (dependency) => getDependencyKey(dependency) === selectedKey
                  );
                  if (!selected) {
                    return null;
                  }

                  const connection = selected.connection_params;
                  return (
                    <dl className="grid gap-2 sm:grid-cols-2">
                      <div>
                        <dt className="text-xs uppercase text-gray-500">Type</dt>
                        <dd className="font-medium text-gray-900">
                          {connection?.type ?? "—"}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-xs uppercase text-gray-500">Host</dt>
                        <dd className="font-medium text-gray-900">
                          {connection?.host ?? "—"}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-xs uppercase text-gray-500">Database</dt>
                        <dd className="font-medium text-gray-900">
                          {connection?.database ?? "—"}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-xs uppercase text-gray-500">Username</dt>
                        <dd className="font-medium text-gray-900">
                          {connection?.username ?? "—"}
                        </dd>
                      </div>
                    </dl>
                  );
                })()}
              </div>
            ) : null}
          </div>
        )}

        {successMessage && (
          <p className="rounded-md border border-green-200 bg-green-50 p-3 text-sm text-green-700">
            {successMessage}
          </p>
        )}
      </div>

      {isOpen && (
        <div
          role="dialog"
          aria-modal="true"
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4"
          onClick={(event) => {
            if (event.target === event.currentTarget && !isSubmitting) {
              handleClose();
            }
          }}
        >
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-6 flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Create SQL Dependency
                </h3>
                <p className="mt-1 text-sm text-gray-600">
                  Provide the connection details for the SQL database.
                </p>
              </div>
              <button
                type="button"
                onClick={handleClose}
                className="rounded-md p-1 text-gray-500 transition hover:text-gray-700"
                aria-label="Close"
                disabled={isSubmitting}
              >
                ×
              </button>
            </div>

            <form className="space-y-4" onSubmit={handleSubmit}>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-gray-700">Type</span>
                  <select
                    value={formState.type}
                    onChange={(event) => handleFieldChange("type", event.target.value)}
                    className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {typeOptions.map((option) => (
                      <option key={option} value={option}>
                        {option.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-gray-700">Port</span>
                  <input
                    type="number"
                    min={1}
                    value={formState.port}
                    onChange={(event) => handleFieldChange("port", event.target.value)}
                    className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </label>

                <label className="flex flex-col gap-2 sm:col-span-2">
                  <span className="text-sm font-medium text-gray-700">Name</span>
                  <input
                    type="text"
                    value={formState.name}
                    onChange={(event) => handleFieldChange("name", event.target.value)}
                    className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    placeholder="Reporting Warehouse"
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-gray-700">Host</span>
                  <input
                    type="text"
                    value={formState.host}
                    onChange={(event) => handleFieldChange("host", event.target.value)}
                    className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    placeholder="db.internal.local"
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-gray-700">Database</span>
                  <input
                    type="text"
                    value={formState.database}
                    onChange={(event) => handleFieldChange("database", event.target.value)}
                    className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    placeholder="analytics"
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-gray-700">Username</span>
                  <input
                    type="text"
                    value={formState.username}
                    onChange={(event) => handleFieldChange("username", event.target.value)}
                    className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    placeholder="readonly"
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm font-medium text-gray-700">Password</span>
                  <input
                    type="password"
                    value={formState.password}
                    onChange={(event) => handleFieldChange("password", event.target.value)}
                    className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </label>
              </div>

              {submitError && (
                <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {submitError}
                </div>
              )}

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={handleClose}
                  className="rounded-md border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm transition hover:bg-gray-100"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
                >
                  {isSubmitting ? "Saving..." : "Save Dependency"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}
